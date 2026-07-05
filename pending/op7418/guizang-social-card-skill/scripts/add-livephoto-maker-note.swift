import Foundation
import ImageIO

guard CommandLine.arguments.count == 4 else {
    fputs("Usage: swift add-livephoto-maker-note.swift <input.jpg> <output.jpg> <asset-id>\n", stderr)
    exit(2)
}

let inputURL = URL(fileURLWithPath: CommandLine.arguments[1])
let outputURL = URL(fileURLWithPath: CommandLine.arguments[2])
let assetIdentifier = CommandLine.arguments[3]

guard let source = CGImageSourceCreateWithURL(inputURL as CFURL, nil) else {
    fputs("Could not open input image\n", stderr)
    exit(1)
}

guard let imageType = CGImageSourceGetType(source) else {
    fputs("Could not determine image type\n", stderr)
    exit(1)
}

let imageCount = CGImageSourceGetCount(source)

guard let destination = CGImageDestinationCreateWithURL(outputURL as CFURL, imageType, imageCount, nil) else {
    fputs("Could not create output image\n", stderr)
    exit(1)
}

for index in 0..<imageCount {
    var properties = (CGImageSourceCopyPropertiesAtIndex(source, index, nil) as? [String: Any]) ?? [:]
    var makerApple = (properties[kCGImagePropertyMakerAppleDictionary as String] as? [String: Any]) ?? [:]
    makerApple["17"] = assetIdentifier
    properties[kCGImagePropertyMakerAppleDictionary as String] = makerApple

    CGImageDestinationAddImageFromSource(destination, source, index, properties as CFDictionary)
}

guard CGImageDestinationFinalize(destination) else {
    fputs("Could not finalize output image\n", stderr)
    exit(1)
}

print("Wrote Apple MakerNote asset identifier: \(assetIdentifier)")
