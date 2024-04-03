# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html)

## [1.2.0] - 2023-12-14

### Added

- Added function on pipeline creation to dynamically select the RTSP transport protocol. We can configure this on the camera_map with the protocol property or update the new env variable.
- Added environment variable called DEFAULT_PROTOCOL which is the default transport protocol over RTSP the video pipelines will be configured at

### Updated

- Updated skaffold profiles to deploy to correct kubecontexts

## [1.1.0] - 2023-11-10

### Added

- Query strings can be specified per camera in camera map for higher quality AXIS camera live stream

## [1.0.4] - 2023-11-06

### Fixed

- Remove resources limits and requests from video pods to prevent cluster capacity issues

## [1.0.3] - 2023-11-01

### Fixed

- Added overlays for OPERATINGSITE environement variable in nginx video

## [1.0.2] - 2023-11-01

### Fixed

- Missed updating VIDEO_TAG environement variables so updated the env as a fieldRef to the manifests app.kubernetes.io/version label value

## [1.0.1] - 2023-11-01

### Fixed

- Fixed issue with label app.kubernetes.io/version not reflecting the true version

## [1.0.0] - 2023-11-01

### Added

- Initial release of kube-video services