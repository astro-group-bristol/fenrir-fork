const std = @import("std");

pub fn build(b: *std.Build) !void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const clippy_dep = b.dependency(
        "clippy",
        .{ .target = target, .optimize = optimize },
    );

    const build_diskimg_multi = b.step("diskimg_multi", "Build diskimg_multi executable");
    const build_diskimg = b.step("diskimg", "Build diskimg executable. Prefer using `diskimg_multi` instead.");

    const diskimg_multi = b.addExecutable(.{
        .root_source_file = b.path("diskimg_multi/main.zig"),
        .name = "diskimg_multi",
        .target = target,
        .optimize = .ReleaseFast,
    });
    diskimg_multi.root_module.addImport("clippy", clippy_dep.module("clippy"));
    diskimg_multi.linkLibCpp();
    diskimg_multi.addIncludePath(b.path("diskimg_multi"));
    diskimg_multi.addCSourceFiles(
        .{
            .root = b.path("diskimg_multi"),
            .flags = &.{
                "-std=c++11",
            },
            .files = &.{
                "img_plane_parallel_multi_new.cpp",
            },
        },
    );
    build_diskimg_multi.dependOn(&b.addInstallArtifact(diskimg_multi, .{}).step);

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
