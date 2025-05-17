/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/system-info",
        destination:
          "https://ethnic-achievement-fits-clan.trycloudflare.com/system-info/",
      },
    ];
  },
};

export default nextConfig;
