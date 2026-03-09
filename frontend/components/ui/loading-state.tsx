import { LoaderCircle } from "lucide-react";

import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

type LoadingStateProps = {
  title: string;
  description: string;
};

export function LoadingState({ title, description }: LoadingStateProps) {
  return (
    <Card className="mx-auto max-w-2xl">
      <CardHeader>
        <div className="mb-4 inline-flex w-fit animate-spin rounded-full bg-primary/10 p-3 text-primary">
          <LoaderCircle className="size-5" />
        </div>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
    </Card>
  );
}
