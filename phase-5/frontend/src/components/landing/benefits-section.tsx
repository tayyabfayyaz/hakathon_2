"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, Clock, Smartphone, Shield, Zap, Users } from "lucide-react";
import { motion } from "framer-motion";

const benefits = [
  {
    icon: CheckCircle,
    title: "Easy Task Management",
    description:
      "Create, organize, and complete tasks with just a few clicks. Our intuitive interface makes task management effortless.",
  },
  {
    icon: Clock,
    title: "Save Time",
    description:
      "Spend less time organizing and more time doing. Quick actions and keyboard shortcuts boost your productivity.",
  },
  {
    icon: Smartphone,
    title: "Works Everywhere",
    description:
      "Access your tasks from any device. Our responsive design ensures a seamless experience on desktop, tablet, and mobile.",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    description:
      "Your data is protected with industry-standard encryption. We never share your information with third parties.",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description:
      "Instant updates and real-time synchronization. No waiting, no lag – just pure productivity.",
  },
  {
    icon: Users,
    title: "Built for Everyone",
    description:
      "Whether you're a student, professional, or team leader, TodoList Pro adapts to your workflow.",
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
    },
  },
};

export function BenefitsSection() {
  return (
    <section id="benefits" className="py-20 md:py-32 bg-muted/50">
      <div className="container px-4 md:px-6">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center space-y-4 mb-16"
        >
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
            Why Choose TodoList Pro?
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Discover the features that make TodoList Pro the perfect choice for managing
            your tasks and boosting your productivity.
          </p>
        </motion.div>

        {/* Benefits Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
        >
          {benefits.map((benefit, index) => (
            <motion.div key={index} variants={itemVariants}>
              <Card className="h-full transition-all hover:shadow-lg hover:-translate-y-1">
                <CardHeader>
                  <div className="flex items-center gap-4">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <benefit.icon className="h-6 w-6 text-primary" />
                    </div>
                    <CardTitle className="text-xl">{benefit.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {benefit.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
