import { SERVER_URL } from '@/consts'
import { IFile, IResponseServerUploadFiles } from '@/types'
import axios, { AxiosResponse } from 'axios'

const $api = axios.create({ baseURL: SERVER_URL })

interface uploadFileProps {
  file: IFile
  fileId: string
  setProgress: (fileName: string, progress: number) => void
  url: string
}

export const uploadFile = async ({
  file,
  fileId,
  setProgress,
  url
}: uploadFileProps) => {
  const formData = new FormData()
  formData.append('file', file.currentFile)
  formData.append('fileId', file.id)
  formData.append('nameVideo', file.name)

  try {
    const response: AxiosResponse<IResponseServerUploadFiles> = await $api.post(
      url,
      formData,
      {
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total!
          )
          setProgress(fileId, percentCompleted)
        },
        withCredentials: true,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    // тот самый костыль, если все будет без багов, просто убери комменты Маша
    // if (response.status === 200) {
    //   setProgress(fileId, 100)
    // }

    console.log('ЭТО ТО ЧТО МНЕ НУЖНО !!! РОДЯ: ', response)

    return response.data
  } catch (error) {
    console.log('ERROR', error)
    throw error
  }
}
