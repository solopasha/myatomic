ARG VERSION=42

FROM registry.fedoraproject.org/fedora-minimal:$VERSION

RUN rm /etc/yum.repos.d/fedora-cisco-openh264.repo && \
    dnf -y up && dnf -y in --setopt=install_weak_deps=False \
            buildah \
            ccache \
            createrepo_c \
            dbus-daemon \
            distribution-gpg-keys \
            file \
            fuse-overlayfs \
            git-core \
            gnupg2 \
            jq \
            mock \
            nosync \
            ostree \
            podman \
            rpm-ostree \
            rpm-sign \
            rpmdevtools \
            rsync \
            selinux-policy-targeted \
            skopeo \
            tar \
            zstd && \
            dnf clean all && \
    useradd -m -G mock builduser
