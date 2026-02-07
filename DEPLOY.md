# Deploying Saamay Backend to Modal

I have configured your backend to run on Modal with GPU acceleration for the Whisper model. Follow these steps to deploy it.

## Prerequisites

1.  **Install Modal CLI:**
    ```bash
    pip install modal
    ```

2.  **Authenticate:**
    ```bash
    modal setup
    ```
    Follow the browser instructions to log in.

## Deployment

1.  **Deploy the App:**
    Run the following command in your terminal from the `saamay_backend` directory:
    ```bash
    modal deploy modal_app.py
    ```

2.  **Get the URL:**
    Visual feedback in the terminal will show you the URL of your deployed app (e.g., `https://your-username--saamay-backend-fastapi-app.modal.run`).

3.  **Update Flutter App:**
    Copy the URL and update your Flutter app's API base URL configuration to point to this new HTTPS endpoint.
    - For WebSockets, replace `https://` with `wss://`.

## Monitoring

-   **Dashboard:** You can view logs and usage metrics in the [Modal Dashboard](https://modal.com/dashboard).
-   **Logs:** To see live logs during development, use:
    ```bash
    modal serve modal_app.py
    ```

## Notes

-   **GPU Usage:** The app effectively uses an NVIDIA T4 GPU for transcription.
-   **Cold Starts:** The first request might take a few seconds while the container starts. Subsequent requests will be much faster.
-   **Cost:** You are billed by Modal for the seconds the GPU container is running.
