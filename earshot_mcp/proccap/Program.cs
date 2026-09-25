// WASAPI *process loopback* capture: records only the audio rendered by one process tree.
// usage: proccap <pid> <out.wav> <stopfile>   (records until <stopfile> exists)
// Prints "STARTED <unix_ms>" once capture is running.
using System.Runtime.InteropServices;
#nullable disable

static class P
{
    [StructLayout(LayoutKind.Sequential)]
    struct ACT_PARAMS { public int ActivationType; public uint TargetProcessId; public int ProcessLoopbackMode; }
    [StructLayout(LayoutKind.Sequential)]
    struct PROPVARIANT_BLOB { public ushort vt; public ushort r1, r2, r3; public uint cbSize; public IntPtr pBlobData; }
    [StructLayout(LayoutKind.Sequential, Pack = 2)]
    struct WAVEFORMATEX { public ushort wFormatTag, nChannels; public uint nSamplesPerSec, nAvgBytesPerSec; public ushort nBlockAlign, wBitsPerSample, cbSize; }

    [ComImport, Guid("1CB9AD4C-DBFA-4c32-B178-C2F568A703B2"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IAudioClient
    {
        [PreserveSig] int Initialize(int shareMode, uint flags, long hnsBuf, long hnsPeriod, ref WAVEFORMATEX fmt, IntPtr session);
        [PreserveSig] int GetBufferSize(out uint n);
        [PreserveSig] int GetStreamLatency(out long l);
        [PreserveSig] int GetCurrentPadding(out uint p);
        [PreserveSig] int IsFormatSupported(int m, IntPtr f, out IntPtr c);
        [PreserveSig] int GetMixFormat(out IntPtr f);
        [PreserveSig] int GetDevicePeriod(out long a, out long b);
        [PreserveSig] int Start();
        [PreserveSig] int Stop();
        [PreserveSig] int Reset();
        [PreserveSig] int SetEventHandle(IntPtr h);
        [PreserveSig] int GetService(ref Guid iid, [MarshalAs(UnmanagedType.IUnknown)] out object o);
    }
    [ComImport, Guid("C8ADBD64-E71E-48a0-A4DE-185C395CD317"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IAudioCaptureClient
    {
        [PreserveSig] int GetBuffer(out IntPtr data, out uint frames, out uint flags, out ulong devPos, out ulong qpc);
        [PreserveSig] int ReleaseBuffer(uint frames);
        [PreserveSig] int GetNextPacketSize(out uint frames);
    }
    [ComImport, Guid("72A22D78-CDE4-431D-B8CC-843A71199B6D"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IActivateAudioInterfaceAsyncOperation
    {
        [PreserveSig] int GetActivateResult(out int hr, [MarshalAs(UnmanagedType.IUnknown)] out object iface);
    }
    [ComImport, Guid("41D949AB-9862-444A-80F6-C261334DA5EB"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IActivateAudioInterfaceCompletionHandler
    {
        [PreserveSig] int ActivateCompleted(IActivateAudioInterfaceAsyncOperation op);
    }
    [ComImport, Guid("94ea2b94-e9cc-49e0-c0ff-ee64ca8f5b90"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IAgileObject { }

    class Handler : IActivateAudioInterfaceCompletionHandler, IAgileObject
    {
        public ManualResetEvent Done = new(false); public object Client; public int Hr;
        public int ActivateCompleted(IActivateAudioInterfaceAsyncOperation op)
        { op.GetActivateResult(out Hr, out Client); Done.Set(); return 0; }
    }

    [DllImport("Mmdevapi.dll", ExactSpelling = true, PreserveSig = true)]
    static extern int ActivateAudioInterfaceAsync([MarshalAs(UnmanagedType.LPWStr)] string path, ref Guid iid, IntPtr pv,
        IActivateAudioInterfaceCompletionHandler h, out IActivateAudioInterfaceAsyncOperation op);
    [DllImport("kernel32")] static extern IntPtr CreateEvent(IntPtr a, bool m, bool i, string n);
    [DllImport("kernel32")] static extern uint WaitForSingleObject(IntPtr h, uint ms);

    [MTAThread]
    static int Main(string[] a)
    {
        uint pid = uint.Parse(a[0]); string outp = a[1], stopf = a[2];
        var ap = new ACT_PARAMS { ActivationType = 1, TargetProcessId = pid, ProcessLoopbackMode = 0 };
        IntPtr pAp = Marshal.AllocHGlobal(Marshal.SizeOf<ACT_PARAMS>()); Marshal.StructureToPtr(ap, pAp, false);
        var pv = new PROPVARIANT_BLOB { vt = 65, cbSize = (uint)Marshal.SizeOf<ACT_PARAMS>(), pBlobData = pAp };
        IntPtr pPv = Marshal.AllocHGlobal(Marshal.SizeOf<PROPVARIANT_BLOB>()); Marshal.StructureToPtr(pv, pPv, false);
        Guid iidAC = typeof(IAudioClient).GUID;
        var h = new Handler();
        int hr = ActivateAudioInterfaceAsync("VAD\\Process_Loopback", ref iidAC, pPv, h, out var op);
        if (hr != 0) { Console.WriteLine($"ERR activate 0x{hr:X}"); return 1; }
        h.Done.WaitOne(); if (h.Hr != 0) { Console.WriteLine($"ERR activate result 0x{h.Hr:X}"); return 1; }
        var ac = (IAudioClient)h.Client;
        const uint rate = 44100; const ushort ch = 2;
        var fmt = new WAVEFORMATEX { wFormatTag = 1, nChannels = ch, nSamplesPerSec = rate, wBitsPerSample = 16, nBlockAlign = (ushort)(ch * 2), nAvgBytesPerSec = rate * ch * 2, cbSize = 0 };
        hr = ac.Initialize(0, 0x00020000 | 0x00040000, 2000000, 0, ref fmt, IntPtr.Zero);
        if (hr != 0) { Console.WriteLine($"ERR init 0x{hr:X}"); return 1; }
        IntPtr ev = CreateEvent(IntPtr.Zero, false, false, null); ac.SetEventHandle(ev);
        Guid iidCC = typeof(IAudioCaptureClient).GUID; ac.GetService(ref iidCC, out object cco); var cc = (IAudioCaptureClient)cco;
        var ms = new MemoryStream(); long written = 0; int blk = ch * 2; long gapFill = 0;
        ac.Start();
        var sw = System.Diagnostics.Stopwatch.StartNew();
        Console.WriteLine($"STARTED {DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}"); Console.Out.Flush();
        while (!File.Exists(stopf))
        {
            WaitForSingleObject(ev, 50);
            while (cc.GetNextPacketSize(out uint n) == 0 && n > 0)
            {
                cc.GetBuffer(out IntPtr d, out uint fr, out uint fl, out _, out _);
                // keep wall-clock alignment: if the engine delivered nothing for a while (target silent), pad zeros
                long expected = (long)(sw.Elapsed.TotalSeconds * rate) - fr;
                if (expected - written > rate / 10) { long z = expected - written; ms.Write(new byte[z * blk]); written += z; gapFill += z; }
                var buf = new byte[fr * blk];
                if ((fl & 2) == 0) Marshal.Copy(d, buf, 0, buf.Length);
                ms.Write(buf); written += fr; cc.ReleaseBuffer(fr);
            }
        }
        ac.Stop();
        long endExp = (long)(sw.Elapsed.TotalSeconds * rate);
        if (endExp > written) { long z = endExp - written; ms.Write(new byte[z * blk]); gapFill += z; written += z; }
        using (var f = new BinaryWriter(File.Create(outp)))
        {
            int dl = (int)ms.Length;
            f.Write("RIFF"u8.ToArray()); f.Write(36 + dl); f.Write("WAVE"u8.ToArray()); f.Write("fmt "u8.ToArray()); f.Write(16);
            f.Write((short)1); f.Write((short)ch); f.Write((int)rate); f.Write((int)(rate * blk)); f.Write((short)blk); f.Write((short)16);
            f.Write("data"u8.ToArray()); f.Write(dl); f.Write(ms.ToArray());
        }
        Console.WriteLine($"DONE frames={written} secs={written / (double)rate:F2} zeroPaddedSecs={gapFill / (double)rate:F2}");
        return 0;
    }
}
