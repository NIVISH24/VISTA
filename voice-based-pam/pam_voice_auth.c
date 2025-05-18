#define _GNU_SOURCE
#include <security/pam_modules.h>
#include <security/pam_ext.h>
#include <syslog.h>
#include <curl/curl.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <string.h>

#define RECORD_CMD   "/usr/bin/arecord"
#define RECORD_ARGS  {"arecord", "-d", "3", "-f", "cd", "/tmp/voice.wav", NULL}
#define API_URL      "https:/services.vistaa.xyz/voice/identify"  /* ← replace */
#define MAX_BUFFER    1024

/* Struct for storing the response data from API */
struct response_data {
    char buffer[MAX_BUFFER];
    size_t size;
};

/* Write callback function for libcurl to store the response data */
size_t write_callback(void *ptr, size_t size, size_t nmemb, void *data) {
    size_t total_size = size * nmemb;
    struct response_data *res_data = (struct response_data *)data;

    if (res_data->size + total_size < MAX_BUFFER - 1) {
        memcpy(res_data->buffer + res_data->size, ptr, total_size);
        res_data->size += total_size;
    }
    res_data->buffer[res_data->size] = '\0';  /* Null-terminate the response */
    return total_size;
}

PAM_EXTERN int pam_sm_authenticate(pam_handle_t *pamh, int flags,
                                   int argc, const char **argv)
{
    int status;
    pid_t pid;
    const char *record_args[] = RECORD_ARGS;
    long http_code = 0;
    CURLcode curl_res;
    struct response_data res_data;
    res_data.size = 0;

    pam_syslog(pamh, LOG_NOTICE, "→ pam_voice_auth: start auth");

    /* 1) Record 3 seconds of audio */
    pam_syslog(pamh, LOG_NOTICE, "→ pam_voice_auth: spawning arecord");
    pid = fork();
    if (pid == 0) {
        execv(RECORD_CMD, (char * const *)record_args);
        _exit(EXIT_FAILURE);
    }
    if (pid < 0) {
        pam_syslog(pamh, LOG_ERR, "pam_voice_auth: fork() failed");
        return PAM_AUTH_ERR;
    }
    waitpid(pid, &status, 0);
    if (!WIFEXITED(status) || WEXITSTATUS(status) != 0) {
        pam_syslog(pamh, LOG_ERR, "pam_voice_auth: arecord failed (exit %d)", WEXITSTATUS(status));
        return PAM_AUTH_ERR;
    }
    pam_syslog(pamh, LOG_NOTICE, "→ pam_voice_auth: audio recorded");

    /* 2) Initialize libcurl */
    curl_global_init(CURL_GLOBAL_DEFAULT);
    CURL *curl = curl_easy_init();
    if (!curl) {
        pam_syslog(pamh, LOG_ERR, "pam_voice_auth: curl_easy_init() failed");
        curl_global_cleanup();
        return PAM_AUTH_ERR;
    }

    pam_syslog(pamh, LOG_NOTICE, "→ pam_voice_auth: sending to API %s", API_URL);

    /* 3) Build multipart POST */
    curl_easy_setopt(curl, CURLOPT_URL, API_URL);
    curl_mime *mime = curl_mime_init(curl);
    curl_mimepart *part = curl_mime_addpart(mime);
    curl_mime_name(part, "file");
    curl_mime_filedata(part, "/tmp/voice.wav");
    curl_easy_setopt(curl, CURLOPT_MIMEPOST, mime);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 5L);

    /* Set callback function to capture API response */
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &res_data);

    /* 4) Perform request */
    curl_res = curl_easy_perform(curl);
    if (curl_res == CURLE_OK) {
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
    } else {
        pam_syslog(pamh, LOG_ERR, "pam_voice_auth: curl error: %s", curl_easy_strerror(curl_res));
    }

    pam_syslog(pamh, LOG_NOTICE, "→ pam_voice_auth: API responded %ld", http_code);
    pam_syslog(pamh, LOG_NOTICE, "→ pam_voice_auth: API response body: %s", res_data.buffer);

    /* Cleanup */
    curl_mime_free(mime);
    curl_easy_cleanup(curl);
    curl_global_cleanup();

    /* 5) Process API response */
    if (curl_res == CURLE_OK && http_code == 200) {
        /* Check the response to see if it's a success or failure */
        if (strstr(res_data.buffer, "\"result\":\"known\"") != NULL) {
            pam_syslog(pamh, LOG_NOTICE, "→ pam_voice_auth: authentication SUCCESS");
            return PAM_SUCCESS;
        } else if (strstr(res_data.buffer, "\"result\":\"unknown\"") != NULL) {
            pam_syslog(pamh, LOG_NOTICE, "→ pam_voice_auth: authentication FAILURE (unknown user)");
            return PAM_AUTH_ERR;
        } else {
            pam_syslog(pamh, LOG_ERR, "→ pam_voice_auth: authentication FAILURE (invalid response)");
            return PAM_AUTH_ERR;
        }
    } else {
        pam_syslog(pamh, LOG_ERR, "→ pam_voice_auth: API request failed");
        return PAM_AUTH_ERR;
    }
}

PAM_EXTERN int pam_sm_setcred(pam_handle_t *pamh, int flags,
                              int argc, const char **argv)
{
    return PAM_SUCCESS;
}