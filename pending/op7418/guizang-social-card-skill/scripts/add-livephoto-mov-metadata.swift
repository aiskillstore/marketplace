import Foundation
import AVFoundation
import CoreMedia

guard CommandLine.arguments.count == 4 else {
    fputs("Usage: swift add-livephoto-mov-metadata.swift <input.mov> <output.mov> <asset-id>\n", stderr)
    exit(2)
}

let inputURL = URL(fileURLWithPath: CommandLine.arguments[1])
let outputURL = URL(fileURLWithPath: CommandLine.arguments[2])
let assetIdentifier = CommandLine.arguments[3]

try? FileManager.default.removeItem(at: outputURL)

func quickTimeMetadataItem(key: String, value: NSCopying & NSObjectProtocol, dataType: String) -> AVMutableMetadataItem {
    let item = AVMutableMetadataItem()
    item.keySpace = .quickTimeMetadata
    item.key = key as NSString
    item.value = value
    item.dataType = dataType
    return item
}

let asset = AVURLAsset(url: inputURL)
let semaphore = DispatchSemaphore(value: 0)
var didFail = false

Task {
    do {
        let tracks = try await asset.loadTracks(withMediaType: .video)
        guard let videoTrack = tracks.first else {
            throw NSError(domain: "LivePhotoMetadata", code: 1, userInfo: [NSLocalizedDescriptionKey: "No video track"])
        }

        let reader = try AVAssetReader(asset: asset)
        let readerOutput = AVAssetReaderTrackOutput(track: videoTrack, outputSettings: nil)
        readerOutput.alwaysCopiesSampleData = false
        guard reader.canAdd(readerOutput) else {
            throw NSError(domain: "LivePhotoMetadata", code: 2, userInfo: [NSLocalizedDescriptionKey: "Cannot add reader output"])
        }
        reader.add(readerOutput)

        let writer = try AVAssetWriter(outputURL: outputURL, fileType: .mov)
        let formatDescriptions = try await videoTrack.load(.formatDescriptions)
        let sourceFormatHint = formatDescriptions.first
        let writerInput = AVAssetWriterInput(mediaType: .video, outputSettings: nil, sourceFormatHint: sourceFormatHint)
        writerInput.expectsMediaDataInRealTime = false
        guard writer.canAdd(writerInput) else {
            throw NSError(domain: "LivePhotoMetadata", code: 3, userInfo: [NSLocalizedDescriptionKey: "Cannot add writer input"])
        }
        writer.add(writerInput)

        let contentIdentifier = quickTimeMetadataItem(
            key: "com.apple.quicktime.content.identifier",
            value: assetIdentifier as NSString,
            dataType: "com.apple.metadata.datatype.UTF-8"
        )
        writer.metadata = [contentIdentifier]

        let metadataSpec: [String: Any] = [
            kCMMetadataFormatDescriptionMetadataSpecificationKey_Identifier as String: "mdta/com.apple.quicktime.still-image-time",
            kCMMetadataFormatDescriptionMetadataSpecificationKey_DataType as String: "com.apple.metadata.datatype.int8"
        ]
        var metadataDescription: CMFormatDescription?
        let status = CMMetadataFormatDescriptionCreateWithMetadataSpecifications(
            allocator: kCFAllocatorDefault,
            metadataType: kCMMetadataFormatType_Boxed,
            metadataSpecifications: [metadataSpec] as CFArray,
            formatDescriptionOut: &metadataDescription
        )
        guard status == noErr, let metadataDescription else {
            throw NSError(domain: "LivePhotoMetadata", code: 4, userInfo: [NSLocalizedDescriptionKey: "Cannot create metadata description"])
        }

        let metadataInput = AVAssetWriterInput(mediaType: .metadata, outputSettings: nil, sourceFormatHint: metadataDescription)
        let metadataAdaptor = AVAssetWriterInputMetadataAdaptor(assetWriterInput: metadataInput)
        guard writer.canAdd(metadataInput) else {
            throw NSError(domain: "LivePhotoMetadata", code: 5, userInfo: [NSLocalizedDescriptionKey: "Cannot add metadata input"])
        }
        writer.add(metadataInput)

        guard writer.startWriting() else {
            throw writer.error ?? NSError(domain: "LivePhotoMetadata", code: 6)
        }
        guard reader.startReading() else {
            throw reader.error ?? NSError(domain: "LivePhotoMetadata", code: 7)
        }

        writer.startSession(atSourceTime: .zero)

        let stillImageTime = quickTimeMetadataItem(
            key: "com.apple.quicktime.still-image-time",
            value: NSNumber(value: Int8(-1)),
            dataType: "com.apple.metadata.datatype.int8"
        )
        let stillGroup = AVTimedMetadataGroup(
            items: [stillImageTime],
            timeRange: CMTimeRange(start: .zero, duration: CMTime(value: 1, timescale: 600))
        )
        guard metadataAdaptor.append(stillGroup) else {
            throw writer.error ?? NSError(domain: "LivePhotoMetadata", code: 8, userInfo: [NSLocalizedDescriptionKey: "Could not append still image time metadata"])
        }
        metadataInput.markAsFinished()

        let queue = DispatchQueue(label: "livephoto.video.writer")
        writerInput.requestMediaDataWhenReady(on: queue) {
            while writerInput.isReadyForMoreMediaData {
                if let sample = readerOutput.copyNextSampleBuffer() {
                    if !writerInput.append(sample) {
                        didFail = true
                        reader.cancelReading()
                        writerInput.markAsFinished()
                        writer.cancelWriting()
                        semaphore.signal()
                        return
                    }
                } else {
                    writerInput.markAsFinished()
                    writer.finishWriting {
                        semaphore.signal()
                    }
                    return
                }
            }
        }
    } catch {
        didFail = true
        fputs("Error: \(error.localizedDescription)\n", stderr)
        semaphore.signal()
    }
}

semaphore.wait()

if didFail {
    exit(1)
}

print("Wrote QuickTime Live Photo metadata: \(assetIdentifier)")
