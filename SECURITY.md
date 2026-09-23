# Security and Data Boundary

BIO-Laya is a public fork. Do not commit private BIO Core code, memory stores, user data, access tokens, credentials, private benchmark exports, or proprietary training data.

Use synthetic fixtures in tests. Keep private fine-tuning datasets and private checkpoints in private storage.

If a secret is committed, revoke or rotate it immediately. Deleting a later commit is not sufficient because Git history may retain it.
