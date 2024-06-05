namespace WebApi.Models
{
    public enum OperationType
    {
        None,
        LoadToDb,
        LoadToMLModel,
        DownloadSubmissionFile,
        GetResultCast, // TODO: как это лучше назвать?
    }
}
