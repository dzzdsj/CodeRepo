// 根据涨跌着色：正红负绿零灰
interface Props {
  value: number
  suffix?: string
  prefix?: string
  className?: string
}

export function ColorText({ value, suffix = '', prefix = '', className = '' }: Props) {
  const color =
    value > 0 ? 'text-up' : value < 0 ? 'text-down' : 'text-flat'
  const sign = value > 0 ? '+' : ''
  return (
    <span className={`${color} ${className}`}>
      {prefix}
      {sign}
      {value.toFixed(2)}
      {suffix}
    </span>
  )
}
