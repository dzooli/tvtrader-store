FROM vault:1.15

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["vault", "server", "-dev", "-config=/vault/config/vault.hcl"]

