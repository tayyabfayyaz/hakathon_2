import { HeroSection } from "@/components/landing/hero-section";
import { BenefitsSection } from "@/components/landing/benefits-section";
import { DemoSection } from "@/components/landing/demo-section";
import { TestimonialsSection } from "@/components/landing/testimonials";

export default function HomePage() {
  return (
    <>
      <HeroSection />
      <DemoSection />
      <BenefitsSection />
      <TestimonialsSection />
    </>
  );
}
