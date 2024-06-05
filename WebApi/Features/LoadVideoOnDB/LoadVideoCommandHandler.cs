using MediatR;
using WebApi.Models;

namespace WebApi.Features.LoadVideoOnDB
{
    public class LoadVideoCommandHandler : IRequestHandler<LoadVideoCommand, OperationInfo>
    {
        // тут будут сервисы, которые необходимо использовать несколько раз в хендлере
        public LoadVideoCommandHandler()
        {
        }

        public async Task<OperationInfo> Handle(LoadVideoCommand request, CancellationToken ct)
        {
            throw new NotImplementedException();
        }
    }
}
