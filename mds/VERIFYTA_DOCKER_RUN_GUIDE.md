# 基于 Docker 的 `verifyta` 运行指南

本文档给出一套可直接照着执行的 `verifyta` Docker 运行方案，目标是满足以下要求：

- 在宿主机系统较老时，仍可稳定运行官方 `verifyta`
- 通过环境变量提供 `UPPAAL_LICENSE_KEY`
- 让同一个 key 在 Docker 场景下持续可用，而不是每次新开容器都重新丢失
- 能稳定对指定模型和查询文件执行 `verifyta`，并获得正确输出

本文档基于以下组合实际验证过：

- UPPAAL `5.0.0` Linux 发行包
- Docker `ubuntu:24.04`
- 通过 Docker 命名卷持久化 `/home/uppaal/.config`

## 结论先行

推荐方案如下：

- 不要把 license key 烘焙进镜像层
- 只在首次激活时通过环境变量传入 `UPPAAL_LICENSE_KEY`
- 把 `/home/uppaal/.config` 挂到 Docker 命名卷
- 首次激活前，先对该命名卷做一次属主初始化
- 以后所有新容器都复用同一个命名卷

这样做的效果是：

- key 不进入镜像层
- lease 会持久化在 Docker volume 里
- `docker run --rm` 删除的是容器，不会删除 volume
- 新起容器时只要继续挂载同一个 volume，就能继续使用已有 lease

## 目录约定

下面的命令默认在你的项目根目录执行。

我们统一使用这几个路径和名字：

```bash
export UPPAAL_VERSION="5.0.0"
export UPPAAL_ZIP_URL="https://download.uppaal.org/uppaal-5.0/uppaal-5.0.0/uppaal-5.0.0-linux64.zip"
export UPPAAL_ZIP_NAME="uppaal-5.0.0-linux64.zip"
export UPPAAL_DIR_NAME="uppaal-5.0.0-linux64"

export UPPAAL_VENDOR_DIR="$PWD/vendor/uppaal"
export UPPAAL_BUILD_DIR="$PWD/.docker/uppaal-verifyta"
export UPPAAL_IMAGE="local/uppaal-verifyta:${UPPAAL_VERSION}"
export UPPAAL_CONFIG_VOLUME="uppaal_verifyta_config"
```

## 第 1 步：准备官方 UPPAAL 发行包

先下载并解压官方 Linux 发行包：

```bash
mkdir -p "$UPPAAL_VENDOR_DIR"
cd "$UPPAAL_VENDOR_DIR"

curl -L "$UPPAAL_ZIP_URL" -o "$UPPAAL_ZIP_NAME"
unzip -q "$UPPAAL_ZIP_NAME"

test -x "$UPPAAL_VENDOR_DIR/$UPPAAL_DIR_NAME/bin/verifyta" || {
  echo "verifyta binary not found after unzip." >&2
  exit 1
}
```

执行完成后，目录结构应该至少包含：

```text
vendor/uppaal/uppaal-5.0.0-linux64/
├── bin/
│   ├── verifyta
│   └── verifyta.sh
├── demo/
├── lib/
├── res/
└── uppaal.jar
```

## 第 2 步：准备 Docker 构建文件

创建构建目录：

```bash
mkdir -p "$UPPAAL_BUILD_DIR"
```

写入 `Dockerfile`：

```bash
cat > "$UPPAAL_BUILD_DIR/Dockerfile" <<'EOF'
FROM ubuntu:24.04

RUN useradd -ms /bin/bash uppaal
RUN apt-get -qq update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq install -y ca-certificates >/dev/null && \
    rm -rf /var/lib/apt/lists/*

# verifyta 在容器内会探测这两个目录；最小容器里通常不存在。
RUN mkdir -p /dev/disk/by-uuid /dev/disk/by-id && \
    ln -sf /dev/null /dev/disk/by-uuid/FAKE-UUID && \
    ln -sf /dev/null /dev/disk/by-id/FAKE-ID

USER uppaal
ENV USER=uppaal
WORKDIR /home/uppaal

COPY --chown=uppaal:uppaal docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
COPY --chown=uppaal:uppaal uppaal/ /home/uppaal/uppaal/

ENV PATH="/home/uppaal/uppaal/bin:${PATH}"

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["verifyta.sh", "--version"]
EOF
```

写入 `docker-entrypoint.sh`：

```bash
cat > "$UPPAAL_BUILD_DIR/docker-entrypoint.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

LEASE_ROOT="${HOME}/.config/uppaal"
LEASE_HOURS="${UPPAAL_LEASE_HOURS:-168}"

mkdir -p "${LEASE_ROOT}"

shopt -s nullglob
lease_files=("${LEASE_ROOT}"/lease-*)
shopt -u nullglob

if [ "${#lease_files[@]}" -eq 0 ]; then
  if [ -z "${UPPAAL_LICENSE_KEY:-}" ]; then
    echo "No local UPPAAL lease found in ${LEASE_ROOT}." >&2
    echo "Set UPPAAL_LICENSE_KEY for first-time activation." >&2
    exit 2
  fi

  echo "No lease found. Activating verifyta with UPPAAL_LICENSE_KEY..." >&2
  verifyta.sh --key "${UPPAAL_LICENSE_KEY}" --lease "${LEASE_HOURS}"
fi

exec "$@"
EOF
chmod +x "$UPPAAL_BUILD_DIR/docker-entrypoint.sh"
```

把官方发行包拷到构建目录：

```bash
rm -rf "$UPPAAL_BUILD_DIR/uppaal"
cp -R "$UPPAAL_VENDOR_DIR/$UPPAAL_DIR_NAME" "$UPPAAL_BUILD_DIR/uppaal"
```

## 第 3 步：构建 Docker 镜像

```bash
docker build -t "$UPPAAL_IMAGE" "$UPPAAL_BUILD_DIR"
```

构建成功后，你可以先做一个最小检查：

```bash
docker run --rm "$UPPAAL_IMAGE"
```

如果此时你还没有传 `UPPAAL_LICENSE_KEY`，它应该失败并提示：

- 没有本地 lease
- 需要设置 `UPPAAL_LICENSE_KEY`

这正是我们想要的行为。

## 第 4 步：创建持久化 volume

创建一个 Docker 命名卷，用来保存 lease：

```bash
docker volume create "$UPPAAL_CONFIG_VOLUME"
```

这个 volume 会被挂载到容器里的：

```text
/home/uppaal/.config
```

`verifyta` 的 lease 和配置会写到这里，后续新容器只要继续挂这个 volume，就能继续复用。

### 第 4.1 步：初始化 volume 权限

这是一个真实踩坑点，不能省略。

由于镜像里的 `uppaal` 用户不是 `root`，而 Docker named volume 初始通常归 `root` 所有，所以首次激活前要先把 volume 的属主改成镜像里 `uppaal` 用户的 UID/GID。

先查询镜像内用户的 UID/GID：

```bash
export UPPAAL_UID="$(docker run --rm --entrypoint /usr/bin/id "$UPPAAL_IMAGE" -u)"
export UPPAAL_GID="$(docker run --rm --entrypoint /usr/bin/id "$UPPAAL_IMAGE" -g)"
```

然后初始化 volume：

```bash
docker run --rm \
  -v "$UPPAAL_CONFIG_VOLUME:/cfg" \
  ubuntu:24.04 \
  bash -lc "mkdir -p /cfg/uppaal && chown -R ${UPPAAL_UID}:${UPPAAL_GID} /cfg"
```

执行完成后，首次激活才不会在 `/home/uppaal/.config/uppaal` 这里报 `Permission denied`。

## 第 5 步：首次激活

先在当前 shell 里设置你的 key：

```bash
export UPPAAL_LICENSE_KEY="替换成你自己的 key"
export UPPAAL_LEASE_HOURS="168"
```

然后执行首次激活：

```bash
docker run --rm \
  -e UPPAAL_LICENSE_KEY="$UPPAAL_LICENSE_KEY" \
  -e UPPAAL_LEASE_HOURS="$UPPAAL_LEASE_HOURS" \
  -v "$UPPAAL_CONFIG_VOLUME:/home/uppaal/.config" \
  "$UPPAAL_IMAGE"
```

预期输出应包含：

- `Licensed to ...`
- `UPPAAL 5.0.0 ...`

此时 lease 已经写入 volume。

## 第 6 步：验证 lease 是否可跨新容器复用

现在故意不再传 `UPPAAL_LICENSE_KEY`，重新起一个全新容器：

```bash
docker run --rm \
  -v "$UPPAAL_CONFIG_VOLUME:/home/uppaal/.config" \
  "$UPPAAL_IMAGE"
```

如果仍然输出：

- `Licensed to ...`

就说明 lease 已经成功持久化，后续新容器不会因为 `--rm` 而丢失授权。

## 第 7 步：运行你自己的模型和查询

假设你本地有以下文件：

```text
$PWD/models/my_model.xml
$PWD/models/my_query.q
```

那么直接这样运行：

```bash
docker run --rm \
  -v "$UPPAAL_CONFIG_VOLUME:/home/uppaal/.config" \
  -v "$PWD/models:/work" \
  "$UPPAAL_IMAGE" \
  verifyta.sh /work/my_model.xml /work/my_query.q
```

如果你想把输出保存到本地文件：

```bash
docker run --rm \
  -v "$UPPAAL_CONFIG_VOLUME:/home/uppaal/.config" \
  -v "$PWD/models:/work" \
  "$UPPAAL_IMAGE" \
  verifyta.sh /work/my_model.xml /work/my_query.q \
  > "$PWD/models/my_verifyta_output.txt" 2>&1
```

## 第 8 步：完整验通示例

下面这个例子不是“显然满足”的玩具例子，而是一个**故意包含 deadline bug 的时间自动机**，用来验证 Docker + `verifyta` 链路能否真正发现问题。

### 8.1 示例意图

这个模型包含两个模板：

- `worker`
  - 收到 `start?` 后开始工作
  - 必须在 `x <= 5` 时收到 `finish?` 才能到 `Done`
  - 一旦 `x > 5` 仍未完成，就会进入 `Error`
- `env`
  - 收到 `start!` 后开始计时
  - 只会在 `t >= 7` 时才发送 `finish!`

这代表一个真实缺陷：

- 环境只会在第 `7` 个时间单位之后发完成信号
- 但工作者的 deadline 是 `5`
- 所以 `worker.Error` 一定可达

要验证的性质是：

```text
A[] not worker.Error
```

这个性质应该失败，`verifyta` 应该返回 `Formula is NOT satisfied.`

### 8.2 输入文件

创建目录：

```bash
mkdir -p "$PWD/tmp_verifyta_demo"
```

写入模型文件 `buggy_deadline.xml`：

```bash
cat > "$PWD/tmp_verifyta_demo/buggy_deadline.xml" <<'EOF'
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE nta PUBLIC "-//Uppaal Team//DTD Flat System 1.6//EN" "http://www.it.uu.se/research/group/darts/uppaal/flat-1_6.dtd">
<nta>
  <declaration>clock x, t;
chan start, finish;
</declaration>
  <template>
    <name x="5" y="5">Worker</name>
    <declaration></declaration>
    <location id="worker_idle" x="0" y="0">
      <name x="-16" y="-24">Idle</name>
    </location>
    <location id="worker_busy" x="200" y="0">
      <name x="184" y="-24">Busy</name>
      <label kind="invariant" x="168" y="24">x &lt;= 10</label>
    </location>
    <location id="worker_done" x="400" y="-80">
      <name x="388" y="-104">Done</name>
    </location>
    <location id="worker_error" x="400" y="80">
      <name x="384" y="104">Error</name>
    </location>
    <init ref="worker_idle"/>
    <transition>
      <source ref="worker_idle"/>
      <target ref="worker_busy"/>
      <label kind="synchronisation" x="72" y="-32">start?</label>
      <label kind="assignment" x="72" y="-8">x = 0</label>
    </transition>
    <transition>
      <source ref="worker_busy"/>
      <target ref="worker_done"/>
      <label kind="guard" x="252" y="-96">x &lt;= 5</label>
      <label kind="synchronisation" x="252" y="-72">finish?</label>
    </transition>
    <transition>
      <source ref="worker_busy"/>
      <target ref="worker_error"/>
      <label kind="guard" x="252" y="72">x &gt; 5</label>
    </transition>
  </template>
  <template>
    <name x="5" y="165">Environment</name>
    <declaration></declaration>
    <location id="env_before" x="0" y="160">
      <name x="-36" y="136">BeforeStart</name>
    </location>
    <location id="env_running" x="200" y="160">
      <name x="168" y="136">Running</name>
      <label kind="invariant" x="168" y="184">t &lt;= 7</label>
    </location>
    <location id="env_after" x="400" y="160">
      <name x="376" y="136">AfterFinish</name>
    </location>
    <init ref="env_before"/>
    <transition>
      <source ref="env_before"/>
      <target ref="env_running"/>
      <label kind="synchronisation" x="72" y="128">start!</label>
      <label kind="assignment" x="72" y="152">t = 0</label>
    </transition>
    <transition>
      <source ref="env_running"/>
      <target ref="env_after"/>
      <label kind="guard" x="252" y="128">t &gt;= 7</label>
      <label kind="synchronisation" x="252" y="152">finish!</label>
    </transition>
  </template>
  <system>worker = Worker();
env = Environment();
system worker, env;
</system>
  <queries>
  </queries>
</nta>
EOF
```

写入查询文件 `buggy_deadline.q`：

```bash
cat > "$PWD/tmp_verifyta_demo/buggy_deadline.q" <<'EOF'
A[] not worker.Error
EOF
```

### 8.3 运行命令

在已经完成前面镜像构建、volume 创建、volume 权限初始化和首次激活之后，执行：

```bash
docker run --rm \
  -v "$UPPAAL_CONFIG_VOLUME:/home/uppaal/.config" \
  -v "$PWD/tmp_verifyta_demo:/work" \
  "$UPPAAL_IMAGE" \
  verifyta.sh -t0 /work/buggy_deadline.xml /work/buggy_deadline.q
```

这里：

- `-t0` 表示要求 `verifyta` 在性质失败时输出 witness trace
- 这个命令本身不再传 `UPPAAL_LICENSE_KEY`
- 如果它还能正常跑，说明 lease 的持久化已经生效

### 8.4 期望输出

预期输出应包含：

- `Verifying formula 1`
- `Formula is NOT satisfied.`
- `Showing witness trace`
- 某个状态里 `worker.Busy`
- 某个后续迁移里 `worker.Busy->worker.Error`

一次实际跑通时得到的关键输出如下：

```text
Options for the verification:
  Generating some trace
  Search order is breadth first
  Using conservative space optimisation

Verifying formula 1 at /work/buggy_deadline.q:1
 -- Formula is NOT satisfied.
 -- Showing witness trace:

State:
( worker.Idle env.BeforeStart )
x=0 t=0

Transition:
  env.BeforeStart->env.Running { 1, start!, t := 0 }
  worker.Idle->worker.Busy { 1, start?, x := 0 }

State:
( worker.Busy env.Running )
x=0 t=0

Delay: 5.5

State:
( worker.Busy env.Running )
x=5.5 t=5.5

Transition:
  worker.Busy->worker.Error { x > 5, tau, 1 }
```

这说明：

- 系统从 `Idle` / `BeforeStart` 正常启动
- `worker` 进入 `Busy`
- 时间推进到 `5.5`
- 由于 `x > 5`，`worker` 直接进入 `Error`
- 所以查询 `A[] not worker.Error` 被证伪

### 8.5 这个例子为什么适合作为后续验通基线

这个例子适合作为回归 smoke test，因为它同时覆盖了：

- 自定义 XML 模型加载
- 自定义 `.q` 文件加载
- Docker 容器内 `verifyta` 运行
- lease 持久化是否有效
- 失败性质是否能输出 witness trace
- 结果是否真的是“发现问题”，而不是“验证一个显然成立的性质”

## 第 9 步：建议的日常使用方式

推荐你日常都按下面这个模式运行：

```bash
docker run --rm \
  -v "$UPPAAL_CONFIG_VOLUME:/home/uppaal/.config" \
  -v "$PWD:/work" \
  -w /work \
  "$UPPAAL_IMAGE" \
  verifyta.sh 路径/到/模型.xml 路径/到/查询.q
```

例如：

```bash
docker run --rm \
  -v "$UPPAAL_CONFIG_VOLUME:/home/uppaal/.config" \
  -v "$PWD:/work" \
  -w /work \
  "$UPPAAL_IMAGE" \
  verifyta.sh ./models/my_model.xml ./models/my_query.q
```

## 第 10 步：当 lease 过期或需要续租时

如果后续出现：

- 本地 lease 不再有效
- 需要重新绑定
- 需要刷新 lease

那么只要再次把 key 作为环境变量传入并执行一次即可：

```bash
docker run --rm \
  -e UPPAAL_LICENSE_KEY="$UPPAAL_LICENSE_KEY" \
  -e UPPAAL_LEASE_HOURS="168" \
  -v "$UPPAAL_CONFIG_VOLUME:/home/uppaal/.config" \
  "$UPPAAL_IMAGE"
```

## 为什么推荐命名卷，而不是把 key 烘进镜像

不推荐把 key 直接写进 Dockerfile，例如：

```dockerfile
RUN verifyta.sh --key ...
```

原因是：

- key 会出现在镜像构建历史或镜像层中
- 镜像如果被导出、缓存、共享，key 也会随之扩散
- 你以后换 key 或调整 lease，更麻烦

命名卷方案更合适：

- key 只在首次激活时进入容器环境
- lease 持久化在 volume
- 镜像本身不带 key

## 如果你必须把 lease 放到宿主机目录里

有时你可能希望直接看到 lease 文件，而不是存在 Docker volume 中。这时可以改用 bind mount。

例如：

```bash
mkdir -p "$PWD/.docker-data/uppaal-config"
chmod 777 "$PWD/.docker-data/uppaal-config"
```

首次激活：

```bash
docker run --rm \
  -e UPPAAL_LICENSE_KEY="$UPPAAL_LICENSE_KEY" \
  -e UPPAAL_LEASE_HOURS="168" \
  -v "$PWD/.docker-data/uppaal-config:/home/uppaal/.config" \
  "$UPPAAL_IMAGE"
```

之后运行模型：

```bash
docker run --rm \
  -v "$PWD/.docker-data/uppaal-config:/home/uppaal/.config" \
  -v "$PWD/models:/work" \
  "$UPPAAL_IMAGE" \
  verifyta.sh /work/my_model.xml /work/my_query.q
```

注意：

- bind mount 更容易遇到权限问题
- 如果目录不可写，首次激活会失败
- 所以默认还是推荐 Docker named volume

## 常见问题

### 1. 为什么容器里要手工创建 `/dev/disk/by-uuid` 和 `/dev/disk/by-id`

因为最小化 Ubuntu 容器里这两个目录通常不存在，而 `verifyta` 在某些路径上会访问它们。实际测试中，如果不补这两个目录，`verifyta` 在授权或版本路径上可能不稳定。

### 2. 为什么要用 `verifyta.sh` 而不是直接用 `verifyta`

因为官方包里的 `verifyta.sh` 会显式使用发行包自带的 loader 和库，这比直接调用裸 `verifyta` 更稳。特别是在宿主机 `glibc` 比较老时，应优先使用 `verifyta.sh`。

### 3. `docker run --rm` 会不会导致授权丢失

不会，只要：

- 你把 `/home/uppaal/.config` 挂到了同一个 Docker named volume
- 这个 volume 在首次使用前已经做过属主初始化

会丢失授权的情况是：

- 你把 lease 只留在临时容器层里
- 容器删掉后没有任何外部持久化

### 4. 同一个 key 能不能一直用

可以，但前提是：

- 你复用同一个持久化 volume
- lease 没过期，或者你在需要时重新用 key 刷新 lease

### 5. 如何确认当前 volume 里已经有 lease

你可以起一个临时容器检查：

```bash
docker run --rm \
  -v "$UPPAAL_CONFIG_VOLUME:/home/uppaal/.config" \
  --entrypoint /bin/bash \
  "$UPPAAL_IMAGE" \
  -lc 'find /home/uppaal/.config -maxdepth 3 -type f | sed -n "1,50p"'
```

预期会看到类似：

```text
/home/uppaal/.config/uppaal/lease-...
/home/uppaal/.config/uppaal/settings.ini
```

## 一次性完整执行清单

如果你只想无脑照着执行，一次做完，可以按下面顺序直接跑：

```bash
export UPPAAL_VERSION="5.0.0"
export UPPAAL_ZIP_URL="https://download.uppaal.org/uppaal-5.0/uppaal-5.0.0/uppaal-5.0.0-linux64.zip"
export UPPAAL_ZIP_NAME="uppaal-5.0.0-linux64.zip"
export UPPAAL_DIR_NAME="uppaal-5.0.0-linux64"
export UPPAAL_VENDOR_DIR="$PWD/vendor/uppaal"
export UPPAAL_BUILD_DIR="$PWD/.docker/uppaal-verifyta"
export UPPAAL_IMAGE="local/uppaal-verifyta:${UPPAAL_VERSION}"
export UPPAAL_CONFIG_VOLUME="uppaal_verifyta_config"
export UPPAAL_LICENSE_KEY="替换成你自己的 key"
export UPPAAL_LEASE_HOURS="168"

mkdir -p "$UPPAAL_VENDOR_DIR"
cd "$UPPAAL_VENDOR_DIR"
curl -L "$UPPAAL_ZIP_URL" -o "$UPPAAL_ZIP_NAME"
unzip -q "$UPPAAL_ZIP_NAME"
cd -

mkdir -p "$UPPAAL_BUILD_DIR"

cat > "$UPPAAL_BUILD_DIR/Dockerfile" <<'EOF'
FROM ubuntu:24.04
RUN useradd -ms /bin/bash uppaal
RUN apt-get -qq update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq install -y ca-certificates >/dev/null && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /dev/disk/by-uuid /dev/disk/by-id && \
    ln -sf /dev/null /dev/disk/by-uuid/FAKE-UUID && \
    ln -sf /dev/null /dev/disk/by-id/FAKE-ID
USER uppaal
ENV USER=uppaal
WORKDIR /home/uppaal
COPY --chown=uppaal:uppaal docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
COPY --chown=uppaal:uppaal uppaal/ /home/uppaal/uppaal/
ENV PATH="/home/uppaal/uppaal/bin:${PATH}"
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["verifyta.sh", "--version"]
EOF

cat > "$UPPAAL_BUILD_DIR/docker-entrypoint.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
LEASE_ROOT="${HOME}/.config/uppaal"
LEASE_HOURS="${UPPAAL_LEASE_HOURS:-168}"
mkdir -p "${LEASE_ROOT}"
shopt -s nullglob
lease_files=("${LEASE_ROOT}"/lease-*)
shopt -u nullglob
if [ "${#lease_files[@]}" -eq 0 ]; then
  if [ -z "${UPPAAL_LICENSE_KEY:-}" ]; then
    echo "No local UPPAAL lease found in ${LEASE_ROOT}." >&2
    echo "Set UPPAAL_LICENSE_KEY for first-time activation." >&2
    exit 2
  fi
  verifyta.sh --key "${UPPAAL_LICENSE_KEY}" --lease "${LEASE_HOURS}"
fi
exec "$@"
EOF
chmod +x "$UPPAAL_BUILD_DIR/docker-entrypoint.sh"

rm -rf "$UPPAAL_BUILD_DIR/uppaal"
cp -R "$UPPAAL_VENDOR_DIR/$UPPAAL_DIR_NAME" "$UPPAAL_BUILD_DIR/uppaal"

docker build -t "$UPPAAL_IMAGE" "$UPPAAL_BUILD_DIR"
docker volume create "$UPPAAL_CONFIG_VOLUME"

export UPPAAL_UID="$(docker run --rm --entrypoint /usr/bin/id "$UPPAAL_IMAGE" -u)"
export UPPAAL_GID="$(docker run --rm --entrypoint /usr/bin/id "$UPPAAL_IMAGE" -g)"

docker run --rm \
  -v "$UPPAAL_CONFIG_VOLUME:/cfg" \
  ubuntu:24.04 \
  bash -lc "mkdir -p /cfg/uppaal && chown -R ${UPPAAL_UID}:${UPPAAL_GID} /cfg"

docker run --rm \
  -e UPPAAL_LICENSE_KEY="$UPPAAL_LICENSE_KEY" \
  -e UPPAAL_LEASE_HOURS="$UPPAAL_LEASE_HOURS" \
  -v "$UPPAAL_CONFIG_VOLUME:/home/uppaal/.config" \
  "$UPPAAL_IMAGE"
```

完成后，日常运行就是：

```bash
docker run --rm \
  -v "$UPPAAL_CONFIG_VOLUME:/home/uppaal/.config" \
  -v "$PWD:/work" \
  -w /work \
  "$UPPAAL_IMAGE" \
  verifyta.sh ./你的模型.xml ./你的查询.q
```

## 参考

- 官方下载页：<https://uppaal.org/downloads/>
- 官方 `verifyta` 文档：<https://docs.uppaal.org/toolsandapi/verifyta/>
- 官方 Docker 文档：<https://docs.uppaal.org/toolsandapi/docker/>
