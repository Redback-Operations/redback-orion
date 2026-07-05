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