import { TriangleAlert } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

type ErrorStateProps = {
  title?: string;
  description: string;
};

export function ErrorState({
  title = "Something went wrong",
  description,
}: ErrorStateProps) {
  return (
    <Card className="border-danger/20 bg-white/80">
      <CardHeader>
        <div className="mb-4 inline-flex w-fit rounded-2xl bg-danger/10 p-3 text-danger">
          <TriangleAlert className="size-5" />
        </div>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="text-sm text-muted">
        The frontend preserves backend error codes and detail payloads in later commits.
      </CardContent>
    </Card>
  );
}
