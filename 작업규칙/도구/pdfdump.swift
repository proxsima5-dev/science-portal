// pdfdump <pdf> <out-dir> <prefix> [png]
// 쪽마다 글자를 <prefix>_글.md에, png를 주면 쪽 그림을 <out-dir>/<prefix>_쪽/p001.png(2배)로 저장
import Foundation
import PDFKit
import AppKit

let a = CommandLine.arguments
guard a.count >= 4, let doc = PDFDocument(url: URL(fileURLWithPath: a[1])) else {
    FileHandle.standardError.write("pdf를 열지 못했어요\n".data(using: .utf8)!); exit(1)
}
let out = URL(fileURLWithPath: a[2]), prefix = a[3], png = a.count > 4
let fm = FileManager.default
try? fm.createDirectory(at: out, withIntermediateDirectories: true)
let pageDir = out.appendingPathComponent("\(prefix)_쪽")
if png { try? fm.createDirectory(at: pageDir, withIntermediateDirectories: true) }
var md = "# \(prefix) (\(URL(fileURLWithPath: a[1]).lastPathComponent))\n\n"
for i in 0..<doc.pageCount {
    guard let p = doc.page(at: i) else { continue }
    let n = String(format: "p%03d", i + 1)
    md += "## \(n)\n\n" + (p.string ?? "").trimmingCharacters(in: .whitespacesAndNewlines) + "\n\n"
    if png {
        let b = p.bounds(for: .mediaBox)
        let w = Int(b.width * 2), h = Int(b.height * 2)
        let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: w, pixelsHigh: h, bitsPerSample: 8, samplesPerPixel: 4,
                                   hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
        NSGraphicsContext.saveGraphicsState()
        let ctx = NSGraphicsContext(bitmapImageRep: rep)!
        NSGraphicsContext.current = ctx
        ctx.cgContext.setFillColor(NSColor.white.cgColor)
        ctx.cgContext.fill(CGRect(x: 0, y: 0, width: w, height: h))
        ctx.cgContext.scaleBy(x: 2, y: 2)
        p.draw(with: .mediaBox, to: ctx.cgContext)
        NSGraphicsContext.restoreGraphicsState()
        try? rep.representation(using: .png, properties: [:])?.write(to: pageDir.appendingPathComponent("\(n).png"))
    }
}
try? md.write(to: out.appendingPathComponent("\(prefix)_글.md"), atomically: true, encoding: .utf8)
print("\(prefix): \(doc.pageCount)쪽")
