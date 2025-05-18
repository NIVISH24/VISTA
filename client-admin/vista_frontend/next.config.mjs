/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/system-info",
        destination:
          "https://ethnic-achievement-fits-clan.trycloudflare.com/system-info/",
      },
      {
        source: "/api/km/:path*", // NEW proxy route
        destination: "https://services.vistaa.xyz/km/:path*", // Will forward all requests
      },
    ];
  },
};

export default nextConfig;
