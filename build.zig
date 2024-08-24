const std = @import("std");

pub fn build(b: *std.Build) !void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const clippy_dep = b.dependency(
        "clippy",
        .{ .target = target, .optimize = optimize },
    );

    const build_diskimg = b.step("diskimg", "Build diskimg executable");

    const diskimg = b.addExecutable(.{
        .root_source_file = b.path("diskimg/main.zig"),
        .name = "diskimg",
        .target = target,
        .optimize = .ReleaseFast,
    });
    diskimg.root_module.addImport("clippy", clippy_dep.module("clippy"));
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
