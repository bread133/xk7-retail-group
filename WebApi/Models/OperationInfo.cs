using WebApi.Common;

namespace WebApi.Models
{
    /// <summary>
    /// результат операции для MediatR
    /// </summary>
    public class OperationInfo
    {
        /// <summary>
        /// Уникальный идентификатор операции
        /// </summary>
        /// <example>f4d1aecb-59cd-4a38-921e-83201be96e40</example>
        public string Id { get; set; } = default!;
        
        /// <summary>
        /// Дата и время создания операции
        /// </summary>
        /// <example>2024-06-06T01:19:17.995Z</example>
        public DateTime CreatedAt { get; set; }

        /// <summary>
        /// Тип операции
        /// </summary>
        /// <example>LoadToDb</example>
        public OperationType Type { get; set; }

        /// <summary>
        /// Дата и время последнего изменения операции
        /// </summary>
        /// <example>2024-06-06T01:21:17.995Z</example>
        public DateTime LastUpdateAt { get; set; }

        public IReadOnlyCollection<Fault>? Faults { get; set; }
    }
}
