const std = @import("std");
const clippy = @import("clippy").ClippyInterface(.{});

extern fn diskimg_main(c_int, [*c][*c]const u8) c_int;

const Arguments = clippy.Arguments(&.{
    .{
        .arg = "-s/--size size",
        .argtype = usize,
        .help = "Column / row size. The full image with be (size * size). Default: 500.",
    },
    .{
        .arg = "--procs num_procs",
        .argtype = usize,
        .help = "Number of processors to run on: Default: 1",
    },
    .{
        .arg = "--proc-id id",
        .argtype = usize,
        .help = "Number of processors to run on: Default: 0",
    },
    .{
        .arg = "spin",
        .help = "Black hole spin (0-1).",
        .required = true,
    },
    .{
        .arg = "inc",
        .help = "Observer inclination in degrees (0-90).",
        .required = true,
    },
    .{
        .arg = "edd",
        .help = "Eddington ratio.",
        .required = true,
    },
    .{
        .arg = "-o/--outfile prefix",
        .help = "String to prefix the output file with. Defaults: 'diskimg-output'",
    },
});

pub fn main() !u8 {
    // just use an arena for everything so we can cleanup in one go
    const allocator = std.heap.c_allocator;
    var arena = std.heap.ArenaAllocator.init(allocator);
    defer arena.deinit();
    const alloc = arena.allocator();

    const args = try std.process.argsAlloc(alloc);
    defer std.process.argsFree(alloc, args);

    const stdout = std.io.getStdOut().writer();

    for (args) |arg| {
        if (std.mem.eql(u8, arg, "--help")) {
            try Arguments.writeHelp(stdout, .{});
            return 0;
        }
    }

    var itt = clippy.ArgIterator.init(args);
    _ = try itt.next();
    const parsed = try Arguments.parseAll(&itt);

    var arglist = std.ArrayList([*c]const u8).init(alloc);
    defer arglist.deinit();
    try arglist.append(args[0]);
    try arglist.append(try std.fmt.allocPrintZ(
        alloc,
        "{d}",
        .{parsed.size orelse 500},
    ));
    try arglist.append(try std.fmt.allocPrintZ(
        alloc,
        "{d}",
        .{parsed.procs orelse 1},
    ));
    try arglist.append(try std.fmt.allocPrintZ(
        alloc,
        "{d}",
        .{parsed.@"proc-id" orelse 0},
    ));
    try arglist.append(try std.fmt.allocPrintZ(
        alloc,
        "{d}",
        .{parsed.spin},
    ));
    try arglist.append(try std.fmt.allocPrintZ(
        alloc,
        "{d}",
        .{parsed.inc},
    ));
    // hardcode most of the disc configuration:
    try arglist.append("1");
    try arglist.append(try std.fmt.allocPrintZ(
        alloc,
        "{d}",
        .{parsed.edd},
    ));
    try arglist.append(try std.fmt.allocPrintZ(
        alloc,
        "{d}",
        .{parsed.edd},
    ));
    try arglist.append("30");
    try arglist.append(try std.fmt.allocPrintZ(
        alloc,
        "{s}",
        .{parsed.outfile orelse "diskimg-output"},
    ));

    const main_args = try arglist.toOwnedSlice();

    try stdout.writeAll("Arguments parsed: calling into main\n---\n");

    return @intCast(diskimg_main(
        @intCast(main_args.len),
        main_args.ptr,
    ));
}
