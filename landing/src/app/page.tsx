import Hero from "@/components/sections/Hero";
import TechStrip from "@/components/sections/TechStrip";
import Problem from "@/components/sections/Problem";
import HowItWorks from "@/components/sections/HowItWorks";
import SDKSection from "@/components/sections/SDKSection";
import Architecture from "@/components/sections/Architecture";
import DashboardPreview from "@/components/sections/DashboardPreview";
import Timeline from "@/components/sections/Timeline";
import APISection from "@/components/sections/APISection";
import GitHubSection from "@/components/sections/GitHubSection";

export default function Home() {
  return (
    <>
      <Hero />
      <TechStrip />
      <Problem />
      <HowItWorks />
      <SDKSection />
      <Architecture />
      <DashboardPreview />
      <Timeline />
      <APISection />
      <GitHubSection />
    </>
  );
}
