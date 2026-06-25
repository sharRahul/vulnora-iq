import { Bot, User } from "lucide-react";
import type { ChatMessage as ChatMessageType } from "@/types";
import { cn } from "@/lib/utils";

export function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === "user";
  return (
    <div className={cn("flex gap-2", isUser && "flex-row-reverse")}>
      <span
        className={cn(
          "flex size-7 shrink-0 items-center justify-center rounded-md border border-border",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-[color-mix(in_srgb,var(--accent-slate)_16%,transparent)] text-[var(--accent-slate)]",
        )}
      >
        {isUser ? <User className="size-4" /> : <Bot className="size-4" />}
      </span>
      <div
        className={cn(
          "max-w-[82%] rounded-lg border px-3 py-2 text-sm leading-relaxed",
          isUser
            ? "border-transparent bg-primary text-primary-foreground"
            : "border-border bg-card text-foreground",
        )}
      >
        {message.pending ? (
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <span className="flex gap-1">
              <span className="size-1.5 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.3s]" />
              <span className="size-1.5 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.15s]" />
              <span className="size-1.5 animate-bounce rounded-full bg-muted-foreground" />
            </span>
            Thinking…
          </span>
        ) : (
          message.content
        )}
      </div>
    </div>
  );
}
