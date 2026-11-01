ARG VERSION=45

FROM registry.fedoraproject.org/fedora-minimal:$VERSION

RUN rm /usr/share/dnf5/repos.d/fedora-cisco-openh264.repo && \
        dnf -y up && dnf -y in --setopt=install_weak_deps=False \
        buildah \
        createrepo_c \
        distribution-gpg-keys \
        fedora-repos-archive \
        file \
        fuse-overlayfs \
        git-core \
        gnupg2 \
        jq \
        koji \
        ostree \
        podman \
        rpm-ostree \
        rpm-sign \
        selinux-policy-targeted \
        skopeo \
        tar \
        yq \
        zstd && \
        dnf clean all && \
        useradd -M builduser
