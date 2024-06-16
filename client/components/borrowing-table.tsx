'use client'

import { useBorrowingStore } from '@/store/borrowing-store'
import { IVideoBorrowing } from '@/types'
import { BorrowingItem } from './borrowing-item'

export const BorrowingTable = () => {
  const { videoBorrowings } = useBorrowingStore()

  if (!videoBorrowings.length) {
    return null
  }

  return (
    <div className='flex h-full items-center w-full justify-start'>
      <div className='relative w-full h-full flex flex-col items-center justify-center'>
        <div className='flex flex-col w-full h-full'>
          <div className='overflow-x-auto'>
            <div className='align-middle inline-block min-w-full sm:px-6 lg:px-'>
              <div className='shadow overflow-hidden sm:rounded-lg'>
                <table className='min-w-full divide-y divide-slate-600'>
                  <thead className='bg-slate-800'>
                    <tr>
                      <th
                        scope='col'
                        className='px-6 py-3 text-left text-xs font-medium text-slate-400  uppercase tracking-wider'
                      >
                        Название оригинала
                      </th>
                      <th
                        scope='col'
                        className='px-6 py-3 text-left text-xs font-medium text-slate-400  uppercase tracking-wider'
                      >
                        Название заимствования
                      </th>
                      <th
                        scope='col'
                        className='px-6 py-3 text-left text-xs font-medium text-slate-400  uppercase tracking-wider'
                      >
                        Начало оригинала
                      </th>
                      <th
                        scope='col'
                        className='px-6 py-3 text-left text-xs font-medium text-slate-400  uppercase tracking-wider'
                      >
                        Конец оригинала
                      </th>
                      <th
                        scope='col'
                        className='px-6 py-3 text-left text-xs font-medium text-slate-400  uppercase tracking-wider'
                      >
                        Начало заимствования
                      </th>
                      <th
                        scope='col'
                        className='px-6 py-3 text-left text-xs font-medium text-slate-400  uppercase tracking-wider'
                      >
                        Конец заимствования
                      </th>
                    </tr>
                  </thead>
                  <tbody className='relative divide-y divide-slate-600'>
                    {videoBorrowings.map(
                      (item: IVideoBorrowing, index: number) => {
                        return (
                          <BorrowingItem
                            time_license_finish={item.time_license_finish}
                            time_license_start={item.time_license_start}
                            time_piracy_finish={item.time_piracy_finish}
                            time_piracy_start={item.time_piracy_start}
                            title_license={item.title_license}
                            title_piracy={item.title_piracy}
                            key={`${item.title_piracy}${item.title_license}${index}`} // если что это просто уникальный ключ для оптимизации рендера для каждой строки (инфа для бэкендеров)
                          />
                        )
                      }
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
