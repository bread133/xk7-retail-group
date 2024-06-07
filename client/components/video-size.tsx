interface VideoProps {
  size: number
}

export const VideoSize = ({ size }: VideoProps) => {
  const BYTES_IN_MB = 1024 * 1024
  const BYTES_IN_GB = 1024 * 1024 * 1024

  let formattedSize: string
  let unit: string

  if (size < BYTES_IN_GB) {
    // Если размер меньше 1 ГБ, отображаем в МБ
    formattedSize = (size / BYTES_IN_MB).toFixed(2) // Преобразуем байты в мегабайты и округляем до 2 знаков после запятой
    unit = 'МБ'
  } else {
    // Если размер больше или равен 1 ГБ, отображаем в ГБ
    formattedSize = (size / BYTES_IN_GB).toFixed(2) // Преобразуем байты в гигабайты и округляем до 2 знаков после запятой
    unit = 'ГБ'
  }

  return (
    <div>
      {formattedSize} {unit}
    </div>
  )
}
