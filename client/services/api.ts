import { SERVER_URL } from '@/consts'
import { IFile, IResponseServerUploadFiles } from '@/types'
import axios, { AxiosResponse } from 'axios'

const $api = axios.create({ baseURL: SERVER_URL })

interface uploadFileProps {
  file: IFile
  fileId: string
  setProgress: (fileName: string, progress: number) => void
}

export const uploadFile = async ({
  file,
  fileId,
  setProgress
}: uploadFileProps) => {
  const formData = new FormData()
  formData.append('file', file.currentFile)
  formData.append('fileId', file.id)
  formData.append('nameVideo', file.name)

  try {
    const response: AxiosResponse<IResponseServerUploadFiles> = await $api.post(
      '/files',
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

    return response.data
  } catch (error) {
    console.log('ERROR', error)
    throw error
  }
}
