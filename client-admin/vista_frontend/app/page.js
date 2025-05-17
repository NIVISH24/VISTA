import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import About from "@/components/About";
import Services from "@/components/Services";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <div className="bg-[#0c0f0a] text-white scroll-smooth font-sans">
      <Navbar />
      <main>
        <section id="hero" className="min-h-screen">
          <Hero />
        </section>
        <section id="about" className="min-h-screen">
          <About />
        </section>
        <section id="services" className="min-h-screen">
          <Services />
        </section>
        <section id="footer" className="min-h-screen">
          <Footer />
        </section>
      </main>
    </div>
  );
}
