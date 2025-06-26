FROM ubuntu:22.04

# 必要なパッケージをインストール
RUN apt-get update && \
    apt-get install -y openjdk-21-jre-headless wget libstdc++6 && \
    useradd -ms /bin/bash metabase

USER metabase
WORKDIR /home/metabase

# Metabase本体をダウンロード（バージョンは必要に応じて調整）
RUN wget -O metabase.jar https://downloads.metabase.com/v0.55.2/metabase.jar

EXPOSE 3000
ENTRYPOINT ["java", "-jar", "metabase.jar"] 