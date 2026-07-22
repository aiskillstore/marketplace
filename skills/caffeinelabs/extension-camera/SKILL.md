---
name: extension-camera
description: Web-camera support.
version: 0.1.4
compatibility:
  npm:
    "@caffeineai/camera": "~0.1.1"
caffeineai-subscription: [none]
---

# Camera
Camera extension for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Overview

This skill adds web-camera access via a prefabricated React hook. Supports photo capture, camera switching, and error handling.

# Frontend

For camera support:

There is a prefabricated React hook `@caffeinelabs/camera/hooks/useCamera.ts` that cannot be modified.

```typescript filepath=@caffeinelabs/camera/hooks/useCamera.ts
import { RefObject } from 'react';

export interface CameraConfig {
  // Camera facing mode - 'user' for front camera, 'environment' for back camera
  facingMode?: 'user' | 'environment';
  // Ideal video width and height in pixels
  width?: number;
  height?: number;
  // Image quality for capture (0-1, where 1 is highest quality)
  quality?: number;
  format?: 'image/jpeg' | 'image/png' | 'image/webp';
}

export interface CameraError {
  type: 'permission' | 'not-supported' | 'not-found' | 'unknown' | 'timeout';
  message: string;
}

export interface UseCameraReturn {
  // Whether camera is currently active and streaming
  isActive: boolean;
  // Whether camera is supported in current browser (null while checking)
  isSupported: boolean | null;
  // Current error state, if any
  error: CameraError | null;
  // Whether camera is initializing, starting, switching, or stopping
  isLoading: boolean;
  currentFacingMode: 'user' | 'environment';
  
  // Returns true on success
  startCamera: () => Promise<boolean>;
  stopCamera: () => Promise<void>;
  capturePhoto: () => Promise<File | null>;
  // Returns true on success
  switchCamera: () => (newFacingMode?: 'user' | 'environment') : Promise<boolean>;
  // Returns true on success
  retry: () => Promise<boolean>;
  
  // Ref to attach to video element for camera preview
  videoRef: RefObject<HTMLVideoElement>;
  // Ref to canvas element used for photo capture (can be hidden)
  canvasRef: RefObject<HTMLCanvasElement>;
}

export declare function useCamera(config?: CameraConfig): UseCameraReturn;
```

Usage example:

```
import { useCamera } from '@caffeineai/camera';

function CameraComponent() {
    const { 
        isActive, 
        isSupported, 
        error, 
        isLoading,
        startCamera, 
        stopCamera, 
        capturePhoto,
        switchCamera,
        videoRef, 
        canvasRef 
    } = useCamera({ 
        autoStart: true,
        facingMode: 'environment' 
    });

    if (isSupported === false) {
        return <div>Camera not supported</div>;
    }

    return (
        <div>
            <video 
                ref={videoRef} 
                style={{ width: '100%', height: 'auto' }}
                playsInline
                muted
            />
            <canvas ref={canvasRef} style={{ display: 'none' }} />
            
            {error && <div>Error: {error.message}</div>}
            
            <div>
                <button onClick={startCamera} disabled={isLoading || isActive}>
                    Start Camera
                </button>
                <button onClick={stopCamera} disabled={isLoading || !isActive}>
                    Stop Camera
                </button>
                <button onClick={switchCamera} disabled={isLoading || !isActive}>
                    Switch Camera
                </button>
                <button onClick={capturePhoto} disabled={!isActive}>
                    Take Photo
                </button>
            </div>
        </div>
    );
}
```

Always place a capture button on camera preview!
Always show a camera preview when the user opens the camera
On desktop, make sure that camera cannot be switched. Only 'environment' is working.
Properly display camera error messages in the app.
Do not make camera buttons clickable until the camera is fully initialized and ready.
Ensure the camera preview has explicit, non-zero dimensions (fixed height, min-height, or an aspect-ratio wrapper) so it never collapses due to layout.
Make the preview responsive across screen sizes (e.g., width: 100% with a stable aspect ratio).
