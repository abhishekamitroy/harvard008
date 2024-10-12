"use client";
import { SidebarNav } from "@/components/global/sidebar-nav";
import { Separator } from "@/components/ui/separator";
import { PageHeader1, PageSubHeader1, TypographyP } from "@/components/ui/typography";
import { redirect } from "next/navigation";
import { useAuthContext } from "../(context)/auth-context";

const sidebarNavItems = [
  {
    title: "General",
    href: "/settings/general",
  },
  {
    title: "Profile",
    href: "/settings/profile",
  },
];

interface SettingsLayoutProps {
  children: React.ReactNode;
}

export default function SettingsLayout({ children }: SettingsLayoutProps) {
  const { user } = useAuthContext();
  if (user === "loading") {
    return <TypographyP>Loading...</TypographyP>;
  }
  if (!user) {
    // this is a protected route - only users who are signed in can view this route
    redirect("/");
  }

  return (
    <>
      <div className="space-y-0.5">
        <PageHeader1>Settings</PageHeader1>
        <PageSubHeader1>Manage your account and profile settings.</PageSubHeader1>
      </div>
      <Separator className="my-6" />
      <div className="flex flex-col space-y-8 lg:flex-row lg:space-x-12 lg:space-y-0">
        <aside className="-mx-4 lg:w-1/5">
          <SidebarNav items={sidebarNavItems} />
        </aside>
        <div className="flex-1 lg:max-w-2xl">{children}</div>
      </div>
    </>
  );
}
