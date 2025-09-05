import type { ReactNode } from "react";
import { NavBar } from "@/components/navbar";

function Layout({ children }: { children: ReactNode }) {
  return (
    <>
      <div className="flex flex-col w-full h-dvh">
        <NavBar />
        <div className="flex-1 bg-stone-200/50 p-4">{children}</div>
      </div>
    </>
  );
}

export default Layout;
