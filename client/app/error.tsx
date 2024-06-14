'use client'

export default function ErrorWrapper({ error }: { error: Error }) {
  console.log('ERROR', error)

  return (
    <div className='flex items-center justify-center min-h-screen bg-red-100'>
      <div className='text-center p-6 bg-white shadow-md rounded-md'>
        <h1 className='text-4xl font-bold text-red-600'>
          Что-то пошло не так.
        </h1>
        <p className='mt-4 text-gray-700'>
          Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже.
        </p>
        <button
          onClick={() => window.location.reload()}
          className='mt-6 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition duration-300'
        >
          Перезагрузить страницу
        </button>
      </div>
    </div>
  )
}
