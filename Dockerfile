ARG VERSION=42

FROM registry.fedoraproject.org/fedora-minimal:$VERSION

RUN rm /etc/yum.repos.d/fedora-cisco-openh264.repo && \
    dnf -y up && dnf -y in --setopt=install_weak_deps=False \
            buildah \
            dbus-daemon \
            distribution-gpg-keys \
            file \
            fuse-overlayfs \
            git-core \
            gnupg2 \
            jq \
            ostree \
            podman \
            rpm-ostree \
            selinux-policy-targeted \
            skopeo \
            tar \
            zstd && \
            dnf clean all && \
    useradd -M builduser
