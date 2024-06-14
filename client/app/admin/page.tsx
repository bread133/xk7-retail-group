'use client'

import { FileInput } from '@/components/file-input'
import { useFilesForDbOriginalStore } from '@/store/files-for-db-original-store'

const VideoAdminUpload = () => {
  const { add, filesZus, isLoading } = useFilesForDbOriginalStore()

  return (
    <>
      <section className='mt-20 pb-20 container mx-auto max-w-6xl'>
        <h2 className='text-4xl font-black leading-tight text-gray-900'>
          Загрузите оригинальное видео в базу данных
        </h2>
        <p className=' mb-14 pr-0  text-base text-gray-600 sm:text-lg xl:text-xl lg:pr-20'>
          Пожалуйста, убедитесь, что ваше видео является полностью оригинальным
        </p>

        <FileInput
          className='w-full lg:w-full'
          addFiles={add}
          files={filesZus}
          isLoading={isLoading}
        />
      </section>
    </>
  )
}

export default VideoAdminUpload
