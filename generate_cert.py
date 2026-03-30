from OpenSSL import crypto

# 🔥 Change this to your server IP
SERVER_IP = "10.170.8.47"

k = crypto.PKey()
k.generate_key(crypto.TYPE_RSA, 2048)

cert = crypto.X509()
cert.get_subject().CN = SERVER_IP   # ✅ FIXED
cert.set_serial_number(1000)
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
cert.set_issuer(cert.get_subject())
cert.set_pubkey(k)

# 🔥 Add Subject Alternative Name (VERY IMPORTANT)
cert.add_extensions([
    crypto.X509Extension(
        b"subjectAltName",
        False,
        f"IP:{SERVER_IP}".encode()
    )
])

cert.sign(k, 'sha256')

open("server.crt", "wb").write(
    crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
)

open("server.key", "wb").write(
    crypto.dump_privatekey(crypto.FILETYPE_PEM, k)
)

print("✅ SSL Certificate Generated (Verified Version)")