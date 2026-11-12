export function getFriendlyErrorMessage(errorData: any): string {
    const detail = errorData?.detail;

    if (!detail) {
        return "Something went wrong. Please try again.";
    }

    if (typeof detail === "string") {
        const lowerDetail = detail.toLowerCase();

        if (lowerDetail.includes("invalid authentication")) {
            return "Your session is invalid. Please log in again.";
        }

        if (lowerDetail.includes("not authenticated")) {
            return "You need to log in to continue.";
        }

        if (lowerDetail.includes("not found")) {
            return "The requested item could not be found.";
        }

        if (lowerDetail.includes("already exists")) {
            return "This record already exists.";
        }

        if (lowerDetail.includes("permission")) {
            return "You do not have permission to perform this action.";
        }

        if (lowerDetail.includes("token")) {
            return "Authentication error. Please log in again.";
        }

        return detail;
    }

    if (Array.isArray(detail)) {
        return detail
            .map((item) => item?.msg || "Invalid input")
            .join(", ");
    }

    return "Something went wrong. Please try again.";
}

/** Turns any thrown error (network failure, backend message) into plain wording for users. */
export function getFriendlyThrownMessage(error: unknown): string {
    const raw = error instanceof Error ? error.message : String(error ?? "");
    const lower = raw.toLowerCase();

    if (
        lower.includes("failed to fetch") ||
        lower.includes("networkerror") ||
        lower.includes("load failed")
    ) {
        return "Can't reach the server. Check that the backend is running and try again.";
    }
    if (lower.includes("could not validate") || lower.includes("not authenticated") || lower.includes("401")) {
        return "Your session has expired. Please log out and log in again.";
    }
    if (lower.includes("unable to process video") || lower.includes("unsupported")) {
        return "This video couldn't be processed. Try an MP4 file and upload it again.";
    }
    if (lower.includes("internal server error")) {
        return "The server had a problem processing this video. Please try again in a moment.";
    }
    return raw || "Something went wrong. Please try again.";
}
