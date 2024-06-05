namespace WebApi.Common
{
    public class Fault
    {
        public string Code { get; set; } = null!;

        public string Message { get; set; } = null!;

        public Fault Detail { get; set; }

        public Fault() 
        { }

        public Fault(string code, string? message = null, Fault? detail = null) 
        {
            this.Code = code ?? throw new ArgumentNullException(nameof(code));
            this.Message = message ?? $"Fault {code} has occured";
            this.Detail = detail;
        }

        public static Fault Unknown { get; } = new Fault(nameof(Unknown));
    }
}
