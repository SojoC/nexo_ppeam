interface AlertProps {
  type: 'error' | 'success';
  message: string;
}

export default function Alert({ type, message }: AlertProps) {
  return (
    <div style={type === 'error' ? styles.errorBox : styles.successBox}>
      {message}
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  errorBox: {
    padding: '12px',
    borderRadius: '8px',
    backgroundColor: '#7f1d1d',
    color: '#fecaca',
    fontSize: '14px',
  },
  successBox: {
    padding: '12px',
    borderRadius: '8px',
    backgroundColor: '#065f46',
    color: '#a7f3d0',
    fontSize: '14px',
  },
};
