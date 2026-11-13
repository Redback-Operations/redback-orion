// Key for the video upload/analysis status the dashboard keeps while a user
// moves between pages. It must be cleared on logout so the next sign-in
// starts with a clean page.
export const VIDEO_STATE_KEY = "orion_dashboard_video_state";

export const clearVideoState = () => {
  try {
    sessionStorage.removeItem(VIDEO_STATE_KEY);
  } catch {
    // storage unavailable - nothing to clear
  }
};
