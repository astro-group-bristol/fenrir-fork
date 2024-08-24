const std = @import("std");

pub fn build(b: *std.Build) !void {
    const target = b.standardTargetOptions(.{});

    const build_diskimg = b.step("diskimg", "Build diskimg executable");

    const diskimg = b.addExecutable(.{
        .name = "diskimg",
        .target = target,
        .optimize = .ReleaseFast,
    });
    diskimg.linkLibCpp();
    diskimg.addIncludePath(b.path("diskimg"));
    diskimg.addCSourceFiles(
        .{
            .root = b.path("diskimg"),
            .flags = &.{
                "-std=c++11",
            },
            .files = &.{
                "img_plane_parallel_multi_new.cpp",
            },
        },
    );

    build_diskimg.dependOn(&b.addInstallArtifact(diskimg, .{}).step);
}
