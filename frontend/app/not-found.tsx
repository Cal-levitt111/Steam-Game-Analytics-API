import Link from "next/link";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";

export default function NotFound() {
  return (
    <div className="py-12">
      <EmptyState
        title="Page not found"
        description="The route you requested is not part of the demo frontend."
        actions={
          <Button asChild>
            <Link href="/">Return home</Link>
          </Button>
        }
      />
    </div>
  );
}
