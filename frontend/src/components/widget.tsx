import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function ControlWidget({
  children,
  name,
  value,
  subtitle,
  className,
}: {
  children: React.ReactNode;
  name: string;
  value: string | number | boolean;
  subtitle?: string;
  className?: string;
}) {
  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>
          <h2 className="font-bold text-xl">{name}</h2>
          {subtitle && (
            <h3 className="text-sm font-normal text-muted-foreground">
              {subtitle}
            </h3>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col justify-between h-full">
        <div className="text-center w-full py-4">
          <h2 className="text-xl text-muted-foreground">Current value: </h2>
          <h2 className="text-4xl font-bold">{value}</h2>
        </div>
        <div className="pt-4 w-full">{children}</div>
      </CardContent>
    </Card>
  );
}
