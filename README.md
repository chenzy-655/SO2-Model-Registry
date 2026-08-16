# SO2 Model Registry

SO2 Detection Android 的签名模型仓库。GitHub Releases 中的模型包可以新增或替换比色管、96孔板场景以及回归响应曲线，无需重新安装 APP。

## 发布模型

1. 修改 `models/profiles.json` 并完成回归验证。
2. 增加版本号和严格递增的 `sequence`。
3. 使用本机私钥构建模型包。
4. 把 `dist/model-index.json` 和签名 ZIP 作为同一个 GitHub Release 的附件上传。

```powershell
python tools/build_release.py `
  --version 2026.08.1 `
  --sequence 20260801 `
  --repository OWNER/SO2-Model-Registry `
  --private-key D:\AI_Visual\SO2_Model_Signing\model-signing-private.pem
```

签名私钥不得上传 GitHub、发送到聊天或复制到手机。APP 只保存公开密钥并在激活前执行 ECDSA、SHA-256、引擎版本及 JSON 结构校验。
