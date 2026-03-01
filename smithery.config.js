export default {
  esbuild: {
    external: [
      "onnxruntime-node",
      "onnxruntime-common",
      "onnxruntime-web",
      "@huggingface/transformers",
      "sharp"
    ],
    target: "node18"
  }
}
