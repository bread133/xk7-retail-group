using MediatR;
using WebApi.Models;

namespace WebApi.Features.LoadVideoOnDB
{
    public class LoadVideoCommand : IRequest<OperationInfo>
    {
    }
}
