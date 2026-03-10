import { LoadingState } from "@/components/ui/loading-state";

export default function Loading() {
  return (
    <div className="py-12">
      <LoadingState
        title="Loading the demo"
        description="Preparing the page shell and fetching the latest backend-backed data."
      />
    </div>
  );
}
