---
name: extension-qr-code
description: QR code scanner using the camera.
version: 0.1.4
compatibility:
  npm:
    "@caffeineai/qr-code": "~0.1.1"
    "@caffeineai/camera": "~0.1.1"
caffeineai-subscription: [none]
---

# QR Code Scanner
QR code scanner extension for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Overview

This skill adds QR code scanning using the device camera. Built on top of the camera component with jsQR for decoding.

# Frontend

For QR code scanner support:

There is a prefabricated React hook imported from `@caffeinelabs/qr-code` that cannot be modified.

```typescript filepath=@caffeinelabs/qr-code/src/hooks/useQRScanner.ts
import { RefObject } from 'react';
import { CameraConfig, CameraError } from '@caffeineai/camera';

export interface QRResult {
  // The decoded QR code data
  data: string;
  // Timestamp when the QR code was scanned
  timestamp: number;
}

export interface QRScannerConfig extends CameraConfig {
  // How often to scan for QR codes in milliseconds (default: 100)
  scanInterval?: number;
  // Maximum number of results to keep in history (default: 10)
  maxResults?: number;
  // URL to load jsQR library from (default: jsdelivr CDN)
  jsQRUrl?: string;
}

export interface UseQRScannerReturn {
  // Array of scanned QR codes (newest first)
  qrResults: QRResult[];
  // Whether currently scanning for QR codes
  isScanning: boolean;
  // Whether jsQR library has been loaded
  jsQRLoaded: boolean;
  
  // Camera state (pass-through from useCamera)
  isActive: boolean;
  isSupported: boolean | null;
  error: CameraError | null;
  isLoading: boolean;
  currentFacingMode: 'user' | 'environment';
  
  // Start camera and begin scanning - returns true on success
  startScanning: () => Promise<boolean>;
  // Stop scanning and camera
  stopScanning: () => Promise<void>;
  // Switch camera facing mode - returns true on success
  switchCamera: () => Promise<boolean>;
  // Clear all scan results
  clearResults: () => void;
  // Reset scanner state (stop scanning and clear results)
  reset: () => void;
  // Retry camera initialization after error - returns true on success
  retry: () => Promise<boolean>;
  
  // Ref to attach to video element for camera preview
  videoRef: RefObject<HTMLVideoElement>;
  // Ref to attach to canvas element used for QR processing (can be hidden)
  canvasRef: RefObject<HTMLCanvasElement>;
  
  // Computed state
  // Whether scanner is ready to use (jsQR loaded and camera supported)
  isReady: boolean;
  // Whether scanning can be started (ready + not loading)
  canStartScanning: boolean;
}

export declare function useQRScanner(config?: QRScannerConfig): UseQRScannerReturn;
```

Usage example:

```typescript filepath=example.ts
import { useQRScanner } from '@caffeineai/qr-code';

function QRScannerComponent() {
    const { 
        qrResults,
        isScanning,
        isActive,
        isSupported,
        error,
        isLoading,
        canStartScanning,
        startScanning,
        stopScanning,
        switchCamera,
        clearResults,
        videoRef,
        canvasRef 
    } = useQRScanner({ 
        facingMode: 'environment',
        scanInterval: 100,
        maxResults: 5
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
                <button onClick={startScanning} disabled={!canStartScanning}>
                    Start Scanning
                </button>
                <button onClick={stopScanning} disabled={isLoading || !isActive}>
                    Stop Scanning
                </button>
                {/* Only show switch camera on mobile */}
                {/Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) && (
                    <button onClick={switchCamera} disabled={isLoading || !isActive}>
                        Switch Camera
                    </button>
                )}
            </div>
            
            <div>
                <h3>Results {qrResults.length > 0 && <button onClick={clearResults}>Clear</button>}</h3>
                {qrResults.map(result => (
                    <div key={result.timestamp}>
                        <small>{new Date(result.timestamp).toLocaleTimeString()}</small>
                        <p>{result.data}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
```

Properly display QR scanner error messages in the app.
