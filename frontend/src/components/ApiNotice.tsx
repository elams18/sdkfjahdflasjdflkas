import { AlertCircle } from "lucide-react";

interface ApiNoticeProps {
    title: string;
    message: string;
    onRetry?: () => void;
}

export function ApiNotice({ title, message, onRetry }: ApiNoticeProps) {
    return (
        <section className="notice notice-error" role={onRetry ? "alert" : "status"}>
            <AlertCircle size={18} />
            <div><strong>{title}</strong><span>{message}</span></div>
            {onRetry && (
                <button type="button" className="text-button" onClick={onRetry}>
                    Retry
                </button>
            )}
        </section>
    );
}