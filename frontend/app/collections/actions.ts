"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { z } from "zod";

import { createCollection } from "@/lib/api/collections";
import { isApiError } from "@/lib/api/client";
import { requireSession } from "@/lib/auth/guards";

const createCollectionSchema = z.object({
  name: z.string().trim().min(1, "Name is required.").max(120, "Name must be 120 characters or fewer."),
  description: z
    .string()
    .trim()
    .max(1000, "Description must be 1000 characters or fewer.")
    .optional(),
  visibility: z.enum(["private", "public"]),
});

export type CreateCollectionState = {
  error?: string;
};

export async function createCollectionAction(
  _: CreateCollectionState,
  formData: FormData,
): Promise<CreateCollectionState> {
  const parsed = createCollectionSchema.safeParse({
    name: formData.get("name"),
    description: formData.get("description"),
    visibility: formData.get("visibility"),
  });

  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? "Collection data is invalid." };
  }

  const { token } = await requireSession();

  try {
    const collection = await createCollection(token, {
      name: parsed.data.name,
      description: parsed.data.description || undefined,
      is_public: parsed.data.visibility === "public",
    });

    revalidatePath("/collections");
    revalidatePath("/collections/public");
    redirect(`/collections/${collection.id}`);
  } catch (error) {
    if (isApiError(error)) {
      return { error: error.payload.message };
    }

    if (error instanceof Error) {
      return { error: error.message };
    }

    return { error: "The collection could not be created." };
  }
}
